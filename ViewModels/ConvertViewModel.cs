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
    private void DeleteSelectedFile()
    {
        if(SelectedFile != null && AddedFiles.Contains(SelectedFile))
        {
            AddedFiles.Remove(SelectedFile);
            Debug.WriteLine($"File removed: {SelectedFile.FileName}");
        }
    }
}
