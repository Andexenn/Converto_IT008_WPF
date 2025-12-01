using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Dto.LoginDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Interfaces;

public interface IAuthApi
{
    public Task<SignUpResponse> SignUp(SignUpRequest signUpRequest);
    public Task<bool> CheckMailExisting(string Email);
    public Task<LoginResponse> Login(LoginRequest loginRequest);
}
