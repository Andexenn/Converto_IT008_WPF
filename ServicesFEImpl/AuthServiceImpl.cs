using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Auth.OAuth2.Flows;
using Google.Apis.Auth.OAuth2.Responses;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class AuthServiceImpl : IAuthService
{

    private readonly IAuthApi _authApi;

    public AuthServiceImpl(IAuthApi authApi)
    {
        _authApi = authApi;
    }
    public async Task<SignUpResponse> SignUp(SignUpRequest signUpRequest) => await _authApi.SignUp(signUpRequest);
    public async Task<bool> CheckMailExisting(string Email) => await _authApi.CheckMailExisting(Email);
    public async Task<LoginResponse> Login(LoginRequest loginRequest) => await _authApi.Login(loginRequest);

    public async Task<LoginResponse> SignInWithGoolge() => await _authApi.SignInWithGoolge();
    public async Task<LoginResponse> SignInWithGithub() => await _authApi.SignInWithGithub();
    public async Task<LoginResponse> RefreshAccessTokenAsync(string currentRefreshToken) => await _authApi.RefreshAccessTokenAsync(currentRefreshToken);

}
