using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto.LoginDto;

public class LoginResponse
{
    public string access_token { get; set; } = "";
    public string token_type { get; set; } = "";
    public UserInfo user { get; set; } = null!;
}
