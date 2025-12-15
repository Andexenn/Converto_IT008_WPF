using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto;

public class AddedFileDto
{
    public string FilePath { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public long FileSizeInBytes { get; set; }
    public string FileIcon { get; set; } = string.Empty;
    public string OriginalFileFormat { get; set; } = string.Empty;
    public string ConvertedFileFormat { get; set; } = string.Empty;
}
