using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto;

public partial class AddedFileDto : ObservableObject
{
    public string FilePath { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public long FileSizeInBytes { get; set; }
    public string FileIcon { get; set; } = string.Empty;
    public string OriginalFileFormat { get; set; } = string.Empty;
    [ObservableProperty]
    private string convertedFileFormat = string.Empty;
    public int Width { get; set; }
    public int Height { get; set; }
    public bool MaintainRatio { get; set; }

}
