using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE;

public interface IAuthService
{
    public Task<SignUpResponse> SignUp(SignUpRequest signUpRequest);
    public Task<bool> CheckMailExisting(string Email);
    public Task<LoginResponse> Login(LoginRequest loginRequest);
    public Task<LoginResponse> SignInWithGoolge();
    public Task<LoginResponse> SignInWithGithub();
    public Task<LoginResponse> RefreshAccessTokenAsync(string currentRefreshToken);

}
