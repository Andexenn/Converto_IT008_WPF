using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto.SignUpDto;

public class CheckMailResponse
{
    public bool exists { get; set; }
    public string email { get; set; } = string.Empty;
}
