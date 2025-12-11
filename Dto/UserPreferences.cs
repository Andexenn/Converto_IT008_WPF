using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto;

public class UserPreferences
{
    public string Theme { get; set; } = "Dark";
    public string Language { get; set; } = "en-US";
    public string DefaultOutputFolder { get; set; } = string.Empty;
}
