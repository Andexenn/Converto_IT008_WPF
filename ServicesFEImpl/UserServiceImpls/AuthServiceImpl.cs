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
    public async Task<bool> SignUp(string FirstName, string LastName, string Email, string Password) => await _authApi.SignUp(FirstName, LastName, Email, Password);
}
