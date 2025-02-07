from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, Post
from database import SessionLocal, engine, Base
from schemas import UserCreate, UserLogin, PostCreate, PostUpdate
from auth import get_current_user, get_password_hash, create_access_token, verify_password
from cerbos_client import CerbosClientClass

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    """Dependency that yields a SQLAlchemy database session.
    
    Yields:
        Session: A SQLAlchemy database session that will be automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cerbos():
    """Dependency that provides a Cerbos client instance for authorization checks.
    
    Returns:
        CerbosClientClass: An instance of the Cerbos client for permission checking.
    """
    return CerbosClientClass() 

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user in the system.
    
    Args:
        user (UserCreate): User registration data including username, email, password, and role.
        db (Session): Database session dependency.
    
    Returns:
        dict: Success message upon successful registration.
        
    Raises:
        HTTPException: 400 error if username is already registered.
    """
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and provide an access token.
    
    Args:
        user (UserLogin): User login credentials (username and password).
        db (Session): Database session dependency.
    
    Returns:
        dict: Access token and token type if authentication is successful.
        
    Raises:
        HTTPException: 401 error if credentials are invalid.
    """
    # Verify user credentials
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/posts")
def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), cerbos: CerbosClientClass = Depends(get_cerbos)):
    """Create a new post with authorization check.
    
    Args:
        post (PostCreate): Post data including title and content.
        current_user (User): Currently authenticated user.
        db (Session): Database session dependency.
        cerbos (CerbosClientClass): Cerbos client for authorization checks.
    
    Returns:
        Post: Created post object.
        
    Raises:
        HTTPException: 403 error if user doesn't have permission to create posts.
    """
    # Check if user has permission to create posts
    if not cerbos.check_access(
        principal={"id": str(current_user.id), "roles": [current_user.role.value]},
        resource={"kind": "post", "attr": {"author_id": current_user.id}},
        action="create"
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Create and save new post
    new_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts")
def get_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), cerbos: CerbosClientClass = Depends(get_cerbos)):
    """Retrieve all posts with authorization check.
    
    Args:
        db (Session): Database session dependency.
        current_user (User): Currently authenticated user.
        cerbos (CerbosClientClass): Cerbos client for authorization checks.
    
    Returns:
        list[Post]: List of all posts.
        
    Raises:
        HTTPException: 403 error if user doesn't have permission to read posts.
    """
    # Check if user has permission to read posts
    if not cerbos.check_access(
        principal={"id": str(current_user.id), "roles": [current_user.role.value]},
        resource={"kind": "post", "attr": {"author_id": current_user.id}},
        action="read"
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    posts = db.query(Post).all()
    return posts

@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), cerbos: CerbosClientClass = Depends(get_cerbos)):
    """Retrieve a specific post by ID with authorization check.
    
    Args:
        post_id (int): ID of the post to retrieve.
        db (Session): Database session dependency.
        current_user (User): Currently authenticated user.
        cerbos (CerbosClientClass): Cerbos client for authorization checks.
    
    Returns:
        Post: Requested post object.
        
    Raises:
        HTTPException: 404 if post not found, 403 if user doesn't have permission.
    """
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user has permission to read this post
    if not cerbos.check_access(
        principal={"id": str(current_user.id), "roles": [current_user.role]},
        resource={"kind": "post", "id": str(post.id), "attr": {"author_id": post.author_id}},
        action="read"
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return post

@app.put("/posts/{post_id}")
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), cerbos: CerbosClientClass = Depends(get_cerbos)):
    """Update a specific post with authorization check.
    
    Args:
        post_id (int): ID of the post to update.
        post_update (PostUpdate): Updated post data (title and/or content).
        db (Session): Database session dependency.
        current_user (User): Currently authenticated user.
        cerbos (CerbosClientClass): Cerbos client for authorization checks.
    
    Returns:
        Post: Updated post object.
        
    Raises:
        HTTPException: 
            - 404 if post not found
            - 403 if user doesn't have permission to update the post
    """
    # Check if post exists
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user has permission to update this post
    if not cerbos.check_access(
        principal={"id": str(current_user.id), "roles": [current_user.role]},
        resource={"kind": "post", "id": str(db_post.id), "attr": {"author_id": db_post.author_id}},
        action="update"
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Update only the fields that were provided
    for field, value in post_update.dict(exclude_unset=True).items():
        setattr(db_post, field, value)
    
    # Commit changes to database
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), cerbos: CerbosClientClass = Depends(get_cerbos)):
    """Delete a specific post with authorization check.
    
    Args:
        post_id (int): ID of the post to delete.
        db (Session): Database session dependency.
        current_user (User): Currently authenticated user.
        cerbos (CerbosClientClass): Cerbos client for authorization checks.
    
    Returns:
        dict: Success message confirming post deletion.
        
    Raises:
        HTTPException: 
            - 404 if post not found
            - 403 if user doesn't have permission to delete the post
    """
    # Check if post exists
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user has permission to delete this post
    if not cerbos.check_access(
        principal={"id": str(current_user.id), "roles": [current_user.role]},
        resource={"kind": "post", "id": str(db_post.id), "attr": {"author_id": db_post.author_id}},
        action="delete"
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Delete the post from database
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}