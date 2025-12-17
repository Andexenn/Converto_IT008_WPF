using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Text.Json.Serialization;   

namespace Converto_IT008_WPF.Dto;

public class ConversionRequestDto
{
    [JsonPropertyName("input_paths")]
    public List<string> InputPaths { get; set; } = new List<string>();
    [JsonPropertyName("output_format")]
    public string OutputFormat { get; set; } = string.Empty;
}
