from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import boto3

def home(request):
    return render(request, 'index.html')

def verify(request):
    return render(request, 'verify.html')

def interface(request):
    return render(request, 'interface.html')

# Khởi tạo client AWS Cognito
cognito_client = boto3.client(
    'cognito-idp',
    region_name='us-east-1',  # Ví dụ: 'us-west-2'
    aws_access_key_id='AKIASE5KQ626SKSHSB6B',  # Đặt khóa truy cập AWS của bạn
    aws_secret_access_key='8R1e667gXjiQZuRWtfXdXLN5OdMbM+gMbFkbHOcD'  # Đặt khóa bí mật AWS của bạn
)

@csrf_exempt
def apiLogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            # Xác thực người dùng với AWS Cognito
            response = cognito_client.initiate_auth(
                # UserPoolId='us-east-1_EGRyDFvsq',  # ID của User Pool
                ClientId='5tddikcdaan8e5e365e9djhe16',  # ID của App Client
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )

            # Lấy token đăng nhập từ phản hồi
            access_token = response['AuthenticationResult']['AccessToken']
            return JsonResponse({"message": "Đăng nhập thành công!", "access_token": access_token}, status=200)

        except cognito_client.exceptions.NotAuthorizedException:
            # Trả về lỗi nếu thông tin đăng nhập không đúng
            return JsonResponse({"error": "Sai thông tin đăng nhập!"}, status=400)
        except cognito_client.exceptions.UserNotFoundException:
            # Trả về lỗi nếu người dùng không tồn tại
            return JsonResponse({"error": "Người dùng không tồn tại!"}, status=404)
        except Exception as e:
            # Trả về lỗi cho các trường hợp ngoại lệ khác
            return JsonResponse({"error": "Đã có lỗi xảy ra: " + str(e)}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)



@csrf_exempt
def apiSignup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        name = data.get('name')
        password = data.get('password')
        # email = data.get('email')

        try:
            # Gọi AWS Cognito API để đăng ký người dùng mới
            response = cognito_client.sign_up(
                ClientId='5tddikcdaan8e5e365e9djhe16',  # ClientId của App Client trong Cognito
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': username},
                    {'Name': 'name', 'Value': name},  # Cung cấp tên người dùng
                    # {'Name': 'pass', 'Value': password}
                ]
            )

            request.session['username'] = username

            return JsonResponse({"message": "Đăng ký thành công!"}, status=200)

        except cognito_client.exceptions.UsernameExistsException:
            # Người dùng đã tồn tại
            return JsonResponse({"error": "Tên người dùng đã tồn tại!"}, status=400)
        except cognito_client.exceptions.InvalidPasswordException:
            # Mật khẩu không hợp lệ
            return JsonResponse({"error": "Mật khẩu không hợp lệ!"}, status=400)
        except Exception as e:
            # Các lỗi khác
            return JsonResponse({"error": "Đã có lỗi xảy ra: " + str(e)}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)


@csrf_exempt
def apiVerify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # print(f"Received data: {data}")
        verification_code = data.get('verificationCode')
        username = request.session.get('username') # Lấy từ thông tin đăng ký, hoặc có thể từ session
        if not username:
            return JsonResponse({"error": "Không tìm thấy tên người dùng trong session!"}, status=400)

        try:
            # Xác nhận mã xác thực từ Cognito
            response = cognito_client.confirm_sign_up(
                ClientId='5tddikcdaan8e5e365e9djhe16',  # Thay bằng ClientId của bạn
                Username=username,
                ConfirmationCode=verification_code
            )

            return JsonResponse({"message": "Xác nhận thành công! Bạn có thể đăng nhập."}, status=200)
        except cognito_client.exceptions.CodeMismatchException:
            return JsonResponse({"error": "Mã xác nhận không chính xác!"}, status=400)
        except cognito_client.exceptions.ExpiredCodeException:
            return JsonResponse({"error": "Mã xác nhận đã hết hạn!"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Đã có lỗi xảy ra: {str(e)}"}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)
