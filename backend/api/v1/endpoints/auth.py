# backend/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from backend.core.config import settings
from jose import jwt  # <<< SỬA LẠI DÒNG NÀY
from datetime import datetime, timedelta
from starlette.responses import HTMLResponse 

router = APIRouter()

# --- Cấu hình OAuth ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)
# --- Cấu hình JWT (Dùng cho việc tạo token) ---
SECRET_KEY = "a_super_secret_key_that_should_be_in_env" # Nên đổi và đưa vào .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 ngày

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- API Endpoints ---
@router.get('/login/google')
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_via_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth/google')
async def auth_via_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Could not authorize access token: {e}")

    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="User info not found in token")
    
    access_token = create_access_token(
        data={"sub": user_info['email'], "name": user_info.get('name')}
    )
    
    frontend_url = "http://localhost:8501" # Streamlit sẽ được truy cập qua Nginx ở port 80
    # Trong môi trường Docker, frontend có thể không biết tên miền bên ngoài.
    # An toàn hơn là redirect về trang gốc, Nginx sẽ xử lý phần còn lại.
    # Chúng ta sẽ điều chỉnh URL này sau nếu cần.
    # Tạm thời để là / để redirect về trang chủ do Nginx phục vụ
    response = RedirectResponse(url=f"/?token={access_token}")
    
    return response

from pydantic import BaseModel

class Web3LoginRequest(BaseModel):
    address: str

@router.post("/login/web3", status_code=200)
def login_with_web3(request: Web3LoginRequest):
    """
    Endpoint đơn giản để nhận địa chỉ ví từ frontend cho việc test.
    """
    print(f"✅ [WEB3 LOGIN] Backend đã nhận được địa chỉ ví: {request.address}")
    
    # Sau này chúng ta sẽ xử lý logic xác thực chữ ký và tạo JWT ở đây.
    # Bây giờ, chỉ cần trả về một thông báo thành công.
    return {"status": "success", "message": f"Backend received wallet address: {request.address}"}

@router.get('/login/github')
async def login_via_github(request: Request):
    redirect_uri = request.url_for('auth_via_github')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get('/auth/github')
async def auth_via_github(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Could not authorize access token: {e}")

    resp = await oauth.github.get('user', token=token)
    user_info = resp.json()

    # Lấy email, có thể cần một cuộc gọi API khác nếu email là private
    email = user_info.get("email")
    if not email:
        # Nếu email không public, gọi endpoint /user/emails
        email_resp = await oauth.github.get('user/emails', token=token)
        email_data = email_resp.json()
        primary_email_obj = next((e for e in email_data if e['primary']), None)
        if primary_email_obj:
            email = primary_email_obj['email']
        else:
            email = user_info.get("login") # Fallback to username

    access_token = create_access_token(
        data={"sub": email, "name": user_info.get('name') or user_info.get('login')}
    )

    response = RedirectResponse(url=f"/?token={access_token}")
    return response