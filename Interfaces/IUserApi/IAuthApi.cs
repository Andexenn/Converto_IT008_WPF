using Converto_IT008_WPF.Dto.SignUpDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Interfaces.IUserApi;

public interface IAuthApi
{
    Task<SignUpResponse> SignUp(SignUpRequest signUpRequest);
}
