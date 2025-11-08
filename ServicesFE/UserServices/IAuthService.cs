using Converto_IT008_WPF.Dto.SignUpDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE.UserServices;

public interface IAuthService
{
    public Task<SignUpResponse> SignUp(SignUpRequest signUpRequest);
    public Task<bool> CheckMailExisting(string Email);
}
