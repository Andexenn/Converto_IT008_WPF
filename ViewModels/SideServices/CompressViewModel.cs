using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels.SideServices;

public partial class CompressViewModel : BaseViewModel
{
    [ObservableProperty]
    private ObservableCollection<UploadedFileModel> inputFiles = new ObservableCollection<UploadedFileModel>();

    private int CurrentIndex = 0;

    private readonly ICompressService _compressService;
    private readonly IProcessImageService _processImageService;
    private readonly ITaskService _taskService;

    public enum OutputFolderMode { Default, Custom };

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NotUploaded))]
    private bool uploaded;
    public bool NotUploaded => !Uploaded;

    [ObservableProperty]
    private BitmapImage previewImage;

    [ObservableProperty]
    private bool isDragging;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsNotCompressing))]
    private bool isCompressing;
    public bool IsNotCompressing => !IsCompressing;

    [ObservableProperty]
    private bool isCompressed;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsNotDownloading))]
    private bool isDownloading;
    public bool IsNotDownloading => !IsDownloading;

    [ObservableProperty]
    ObservableCollection<UserTasksDto> userTasks = new ObservableCollection<UserTasksDto>();

    [ObservableProperty]
    ObservableCollection<string> typeFormats = new ObservableCollection<string> { "Image", "Video", "Audio" };

    [ObservableProperty]
    private string selectedTypeFormat;

    [ObservableProperty]
    private OutputFolderMode selectedOutputFolderMode = OutputFolderMode.Default;

    [ObservableProperty]
    private string customOutputFolderPath = string.Empty;

    [ObservableProperty]
    private double sliderValue = 50;

    [ObservableProperty]
    private ObservableCollection<ProcessedFileResultDto> processedFiles = new ObservableCollection<ProcessedFileResultDto>();

    public CompressViewModel(ICompressService compressService, IProcessImageService processImageService, ITaskService taskService)
    {
        SelectedTypeFormat = TypeFormats[0];
        _compressService = compressService;
        _processImageService = processImageService;
        _taskService = taskService;

        _ = GetUserTasks();
    }


    [RelayCommand]
    void DragEnter() { IsDragging = true; }

    [RelayCommand]
    void DragLeave() { IsDragging = false; }

    [RelayCommand]
    void DropFile(object data)
    {
        IsDragging = false;
        try
        {
            string[] files = data as string[];
            if (files != null && files.Length > 0)
            {
                foreach (var file in files)
                {
                    if (!InputFiles.Any(f => f.FilePath == file))
                    {
                        InputFiles.Add(new UploadedFileModel
                        {
                            FileName = Path.GetFileName(file),
                            FilePath = file
                        });
                    }
                }
                Debug.WriteLine($"So luong file hien tai: {InputFiles.Count}");

                if (InputFiles.Count > 0)
                {
                    Uploaded = true;
                    if (PreviewImage == null) UpdatePreviewImage(0);
                }
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error dropping file: {ex.Message}");
        }
    }

    [RelayCommand]
    void PickFile()
    {
        try
        {
            var filter = "";
            if (SelectedTypeFormat == "Image") filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp;*.webp;*.tiff|All Files|*.*";
            else if (SelectedTypeFormat == "Video") filter = "Video Files|*.mp4;*.webm;*.mov;*.avi;*.mkv;*.aac|All Files|*.*";
            else if (SelectedTypeFormat == "Audio") filter = "Audio Files|*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a|All Files|*.*";

            var openFileDialog = new OpenFileDialog
            {
                Multiselect = true,
                Filter = filter,
                Title = "Choose images to compress"
            };

            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                foreach (var file in openFileDialog.FileNames)
                {
                    if (!InputFiles.Any(f => f.FilePath == file))
                    {
                        InputFiles.Add(new UploadedFileModel
                        {
                            FileName = Path.GetFileName(file),
                            FilePath = file
                        });
                    }
                }

                Debug.WriteLine($"So luong file hien tai: {InputFiles.Count}");

                if (InputFiles.Count > 0)
                {
                    Uploaded = true;
                    if (PreviewImage == null) UpdatePreviewImage(InputFiles.Count - 1);
                    else UpdatePreviewImage(CurrentIndex);
                }
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error picking file: {ex.Message}");
        }
    }

    [RelayCommand]
    void ClearUploadFiles()
    {
        InputFiles.Clear();
        Uploaded = false;
        PreviewImage = null;
        CurrentIndex = 0;
        Debug.WriteLine("Upload files cleared.");
    }

    [RelayCommand]
    private void DeleteCurrentPreviewedFile()
    {
        if (InputFiles.Count == 0) return;

        InputFiles.RemoveAt(CurrentIndex);

        if (InputFiles.Count == 0)
        {
            ClearUploadFiles();
        }
        else
        {
            if (CurrentIndex >= InputFiles.Count) CurrentIndex = InputFiles.Count - 1;
            UpdatePreviewImage(CurrentIndex);
        }
    }

    [RelayCommand]
    private void NextPreviewedImage()
    {
        if (InputFiles.Count == 0) return;
        UpdatePreviewImage(CurrentIndex + 1);
    }

    [RelayCommand]
    private void PreviousPreviewedImage()
    {
        if (InputFiles.Count == 0) return;
        UpdatePreviewImage(CurrentIndex - 1);
    }

    [RelayCommand]
    private void ChangeCustomOutputFolder()
    {
        var folderDialog = new FolderBrowserDialog()
        {
            Description = "Select Custom Output Folder",
            ShowNewFolderButton = true
        };

        if (folderDialog.ShowDialog() == DialogResult.OK)
        {
            CustomOutputFolderPath = folderDialog.SelectedPath;
            Debug.WriteLine($"Custom output folder selected: {CustomOutputFolderPath}");
        }
    }

    [RelayCommand]
    private async Task CompressFiles()
    {
        try
        {
            IsCompressing = true;
            var filePathsArray = InputFiles.Select(f => f.FilePath).ToArray();

            Debug.WriteLine($"Starting compressing {filePathsArray.Length} files");

            string quality = "";
            if (SelectedTypeFormat == "Image") { quality = SliderValue == 0 ? "25" : (SliderValue == 50 ? "50" : "75"); }
            else if (SelectedTypeFormat == "Video") { quality = SliderValue == 0 ? "low" : (SliderValue == 50 ? "medium" : "high"); }
            else if (SelectedTypeFormat == "Audio") { quality = SliderValue == 0 ? "32k" : (SliderValue == 50 ? "64k" : "128k"); }

            byte[] response = await _compressService.CompressAsync(filePathsArray, SelectedTypeFormat, quality, quality);

            ProcessedFiles.Clear();

            if (IsZipFile(response))
                _processImageService.ProcessZipResponse(ProcessedFiles, response);
            else
                _processImageService.ProcessSingleImageResponse(ProcessedFiles, response, Path.GetFileNameWithoutExtension(InputFiles[0].FilePath), Path.GetExtension(InputFiles[0].FilePath), "compressed");

        }
        catch (Exception e)
        {
            Debug.WriteLine($"Bug at compress file {e}");
        }
        finally
        {
            IsCompressing = false;
            IsCompressed = true;
        }
    }

    [RelayCommand]
    private async Task DownloadFiles()
    {
        try
        {
            IsDownloading = true;
            if (SelectedOutputFolderMode == OutputFolderMode.Custom && !string.IsNullOrEmpty(CustomOutputFolderPath))
            {
                await _processImageService.DownloadImages(ProcessedFiles, CustomOutputFolderPath);
            }
            else
                await _processImageService.DownloadImages(ProcessedFiles);
        }
        catch (Exception e)
        {
            Debug.WriteLine($"Bug at download file {e}");
        }
        finally
        {
            IsDownloading = false;
        }
    }

    private bool IsZipFile(byte[] data)
    {
        if (data.Length < 2) return false;
        return data[0] == 0x50 && data[1] == 0x4B;
    }

    private async Task GetUserTasks()
    {
        try
        {
            IsBusy = true;
            var tasks = await _taskService.GetUserTasksAsync();
            var filteredTasks = tasks.Where(t => t.ServiceTypeID == 2).ToList();
            UserTasks = new ObservableCollection<UserTasksDto>(filteredTasks);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error fetching user tasks: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void UpdatePreviewImage(int index)
    {
        if (InputFiles.Count == 0)
        {
            PreviewImage = null;
            return;
        }

        if (index >= InputFiles.Count) index = 0;
        if (index < 0) index = InputFiles.Count - 1;

        CurrentIndex = index;
        PreviewImage = LoadBitmapImage(InputFiles[CurrentIndex].FilePath);
    }

    private BitmapImage LoadBitmapImage(string path)
    {
        var bitmap = new BitmapImage();
        try
        {
            bitmap.BeginInit();
            bitmap.CacheOption = BitmapCacheOption.OnLoad;
            bitmap.UriSource = new Uri(path, UriKind.RelativeOrAbsolute);
            bitmap.EndInit();
            bitmap.Freeze();
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error loading bitmap: {ex.Message}");
            return null;
        }
        return bitmap;
    }
}

public class UploadedFileModel
{
    public string FileName { get; set; }
    public string FilePath { get; set; }
}