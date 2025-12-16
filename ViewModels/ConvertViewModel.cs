using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels;

public partial class ConvertViewModel : BaseViewModel
{
    private string[] filepaths = { };
    [ObservableProperty]
    private ObservableCollection<AddedFileDto> addedFiles = new ObservableCollection<AddedFileDto>();
    [ObservableProperty]
    private ObservableCollection<string> inputCategories = new ObservableCollection<string>
    {
        "Image", "Video", "Audio", "Document"
    };

    [ObservableProperty]
    private ObservableCollection<string> imageFormat = new ObservableCollection<string>()
    {
        ".JPG",
        ".JPEG",
        ".PNG",
        ".BMP",
        ".GIF",
        ".TIFF",
        ".WEBP"
    };
    [ObservableProperty]
    private ObservableCollection<string> videoFormat = new ObservableCollection<string>()
    {
        ".MP4",
        ".AVI",
        ".MOV",
        ".WMV",
        ".FLV",
        ".MKV",
        ".GIF"
    };

    [ObservableProperty]
    private ObservableCollection<string> audioFormat = new ObservableCollection<string>()
    {
        ".MP3",
        ".WAV",
        ".AAC",
        ".FLAC",
        ".OGG",
        ".WMA"
    };
    [ObservableProperty]
    private ObservableCollection<string> documentFormat = new ObservableCollection<string>()
    {
        ".DOCX",
        ".XLSX",
        ".PPTX"
    };

    [ObservableProperty]
    private string selectedInputCategory;

    [ObservableProperty]
    private ObservableCollection<string> availableOutputFormats = new ObservableCollection<string>();

    [ObservableProperty]
    private string selectedOutputFormat;

    [ObservableProperty]
    AddedFileDto selectedFile;

    [ObservableProperty]
    private bool isResizeEnabled;

    [ObservableProperty]
    private bool maintainAspectRatio = true;

    [ObservableProperty]
    private int targetWidth;

    [ObservableProperty]
    private int targetHeight;

    // Preview Image/Video
    [ObservableProperty]
    private bool isImagePreviewVisible;

    [ObservableProperty]
    private bool isVideoPreviewVisible;

    [ObservableProperty]
    private bool isPlaceholderVisible;

    partial void OnSelectedInputCategoryChanged(string value)
    {
        UpdateOutputFormats(value);
    }

    private void UpdateOutputFormats(string category)
    {
        AvailableOutputFormats.Clear();
        IEnumerable<string> source = null;

        switch (category)
        {
            case "Image": source = ImageFormat; break;
            case "Video": source = VideoFormat; break;
            case "Audio": source = AudioFormat; break;
            case "Document": source = DocumentFormat; break;
            default: source = ImageFormat; break;
        }

        if (source != null)
        {
            foreach (var item in source) AvailableOutputFormats.Add(item);
        }

        if (AvailableOutputFormats.Count > 0)
            SelectedOutputFormat = AvailableOutputFormats[0];
    }

    private readonly IConvertService _convertService;
    public ConvertViewModel(IConvertService convertService)
    {
        _convertService = convertService;

        if (InputCategories.Count > 0)
        {
            SelectedInputCategory = InputCategories[0];
        }
    }

    [RelayCommand]
    private void PickFile()
    {
        try
        {
            using (var openFileDiaglog = new OpenFileDialog())
            {
                openFileDiaglog.Multiselect = true;
                var result = openFileDiaglog.ShowDialog();
                if (result == DialogResult.OK)
                {
                    foreach(string file in openFileDiaglog.FileNames)
                    {
                        AddedFileDto addedFile = new AddedFileDto();
                        addedFile.FilePath = file;
                        addedFile.FileName = System.IO.Path.GetFileName(file);
                        addedFile.FileSizeInBytes = new System.IO.FileInfo(file).Length;
                        addedFile.OriginalFileFormat = System.IO.Path.GetExtension(file).ToLower();

                        if(ImageFormat.Contains(addedFile.OriginalFileFormat.ToUpper()))
                            addedFile.FileIcon = "Image";
                        else if(VideoFormat.Contains(addedFile.OriginalFileFormat.ToUpper()))
                            addedFile.FileIcon = "Video";
                        else if(AudioFormat.Contains(addedFile.OriginalFileFormat.ToUpper()))
                            addedFile.FileIcon = "Music";
                        else if(DocumentFormat.Contains(addedFile.OriginalFileFormat.ToUpper()))
                        {
                            if(addedFile.OriginalFileFormat.ToUpper() == ".DOCX")
                                addedFile.FileIcon = "FileWordOutline";
                            else if(addedFile.OriginalFileFormat.ToUpper() == ".XLSX")
                                addedFile.FileIcon = "FileExcelOutline";
                            else if(addedFile.OriginalFileFormat.ToUpper() == ".PPTX")
                                addedFile.FileIcon = "FilePowerpointOutline";
                        }

                        addedFile.ConvertedFileFormat = addedFile.OriginalFileFormat;

                        AddedFiles.Add(addedFile);

                        Debug.WriteLine($"1 file added: {addedFile.FileName}-{addedFile.OriginalFileFormat}-{addedFile.FileIcon}-{addedFile.FileSizeInBytes}");

                    }
                }
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Error picking file: {ex.Message}");
        }
    }

    [RelayCommand]
    private void DeleteFile(AddedFileDto file)
    {
        if (file != null && AddedFiles.Contains(file))
        {
            if (SelectedFile == file)
            {
                SelectedFile = null;

                IsImagePreviewVisible = false;
                IsVideoPreviewVisible = false;
                IsPlaceholderVisible = false;
            }

            AddedFiles.Remove(file);
            Debug.WriteLine($"File removed: {file.FileName}");
        }
    }

    [ObservableProperty]
    private double zoomScale = 1.0;

    [RelayCommand]
    private void ZoomIn()
    {
        if (ZoomScale < 5.0)
        {
            ZoomScale += 0.1;
        }
    }

    [RelayCommand]
    private void ZoomOut()
    {
        if (ZoomScale > 0.2)
        {
            ZoomScale -= 0.1;
        }
    }

    private double _originalAspectRatio = 0;
    private bool _isAdjustingDimensions = false;

    partial void OnSelectedFileChanged(AddedFileDto value)
    {
        IsImagePreviewVisible = false;
        IsVideoPreviewVisible = false;
        IsPlaceholderVisible = false;

        _originalAspectRatio = 0;
        TargetWidth = 0;
        TargetHeight = 0;
        if (value == null || string.IsNullOrEmpty(value.FilePath)) return;

        string ext = value.OriginalFileFormat.ToUpper();

        if (ImageFormat.Contains(ext))
        {
            IsImagePreviewVisible = true;
            try
            {
                using (var stream = new System.IO.FileStream(value.FilePath, System.IO.FileMode.Open, System.IO.FileAccess.Read))
                {
                    var decoder = System.Windows.Media.Imaging.BitmapDecoder.Create(stream, System.Windows.Media.Imaging.BitmapCreateOptions.DelayCreation, System.Windows.Media.Imaging.BitmapCacheOption.None);
                    var frame = decoder.Frames[0];
                    _originalAspectRatio = (double)frame.PixelWidth / frame.PixelHeight;
                    _isAdjustingDimensions = true;
                    TargetWidth = frame.PixelWidth;
                    TargetHeight = frame.PixelHeight;
                    _isAdjustingDimensions = false;
                }
            }
            catch (System.Exception ex) { System.Diagnostics.Debug.WriteLine(ex.Message); }
        }
        else if (VideoFormat.Contains(ext))
        {
            IsVideoPreviewVisible = true;
        }
        else
        {
            IsPlaceholderVisible = true;
        }
    }

    partial void OnTargetWidthChanged(int value)
    {
        if (_isAdjustingDimensions || !MaintainAspectRatio || _originalAspectRatio == 0) return;

        _isAdjustingDimensions = true;
        TargetHeight = (int)(value / _originalAspectRatio);
        _isAdjustingDimensions = false;
    }

    partial void OnTargetHeightChanged(int value)
    {
        if (_isAdjustingDimensions || !MaintainAspectRatio || _originalAspectRatio == 0) return;

        _isAdjustingDimensions = true;
        TargetWidth = (int)(value * _originalAspectRatio);
        _isAdjustingDimensions = false;
    }

    partial void OnMaintainAspectRatioChanged(bool value)
    {
        if (value)
        {
            OnTargetWidthChanged(TargetWidth);
        }
    }
}
