using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Config;

public class AppConfig
{
    public string GoogleClientID { get; set; } = string.Empty;
    public string GoogleClientSecret { get; set; } = string.Empty;
    public string BaseURL { get; set; } = string.Empty;
    public string GithubClientID { get; set; } = string.Empty;
    public string GithubClientSecret { get; set; } = string.Empty;
}
