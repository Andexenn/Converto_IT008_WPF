using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Interfaces.IUserApi;
using Converto_IT008_WPF.ServicesFE.UserServices;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl.UserServiceImpls;

public class AuthServiceImpl : IAuthService
{
    private readonly IAuthApi _authApi;
    public AuthServiceImpl(IAuthApi authApi)
    {
        _authApi = authApi;
    }
    public async Task<SignUpResponse> SignUp(SignUpRequest signUpRequest) => await _authApi.SignUp(signUpRequest);
    public async Task<bool> CheckMailExisting(string Email) => await _authApi.CheckMailExisting(Email);
}
