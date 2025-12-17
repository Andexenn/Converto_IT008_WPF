using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto;

public class ApiErrorResponseDto
{
    [JsonPropertyName("detail")]
    public string? Detail { get; set; }
}
