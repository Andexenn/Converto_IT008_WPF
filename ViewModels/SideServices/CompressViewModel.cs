using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Printing;
using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels.SideServices;

public partial class CompressViewModel : BaseViewModel
{
    private string[] _filepaths = { };
    private int NextIndex;
    private int PreviousIndex;
    private readonly ICompressService _compressService;
    private readonly IProcessImageService _processImageService;
    private readonly ITaskService _taskService;
    public enum OutputFolderMode
    {
        Default,
        Custom
    };

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
    ObservableCollection<string> typeFormats = new ObservableCollection<string>
    {
        "Image",
        "Video",
        "Audio",
    };
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
    void OnDragEnter()
    {
        IsDragging = true;
    }

    [RelayCommand]
    void OnDragLeave()
    {
        IsDragging = false;
    }


    [RelayCommand]
    void DropFile(object data)
    {
        IsDragging = false;
        try
        {
            string[] files = data as string[];
            if (files != null && files.Length > 0)
            {
                _filepaths = files;
                Debug.WriteLine($"So luong file drop: {_filepaths.Length}");
                Uploaded = true;
                PreviewImage = LoadBitmapImage(_filepaths[0]);
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
            var openFileDialog = new OpenFileDialog
            {
                Multiselect = true,
                Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp;*.webp|All Files|*.*",
                Title = "Choose images to compress"
            };

            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                _filepaths = openFileDialog.FileNames;
                Debug.WriteLine($"File picked: {_filepaths[0]}");
                Debug.WriteLine($"So luong file drop: {_filepaths.Length}");

                Uploaded = true;
                PreviewImage = LoadBitmapImage(_filepaths[0]);
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
        _filepaths = Array.Empty<string>();
        Uploaded = false;
        PreviewImage = null;
        Debug.WriteLine("Upload files cleared.");
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


    [RelayCommand]
    private void NextPreviewedImage()
    {
        NextIndex = (NextIndex + 1) % _filepaths.Length;
        Debug.WriteLine($"{NextIndex}");
        PreviewImage = LoadBitmapImage(_filepaths[NextIndex]);
    }

    [RelayCommand]
    private void PreviousPreviewedImage()
    {
        PreviousIndex = (PreviousIndex - 1 + _filepaths.Length) % _filepaths.Length;
        Debug.WriteLine($"{PreviousIndex}");
        PreviewImage = LoadBitmapImage(_filepaths[PreviousIndex]);
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
            Debug.WriteLine($"Starting compressing {_filepaths.Length} files");
            byte[] response = await _compressService.CompressAsync(_filepaths, SelectedTypeFormat, SliderValue.ToString(), SliderValue.ToString());

            ProcessedFiles.Clear();

            if(IsZipFile(response))
                _processImageService.ProcessZipResponse(ProcessedFiles, response);
            else
                _processImageService.ProcessSingleImageResponse(ProcessedFiles, response);

        }
        catch(Exception e)
        {
            Debug.WriteLine($"Bug at compress file {e}");
        }
        finally
        {
            IsCompressing = false;
            IsCompressed = true;
        }

    }

    private bool IsZipFile(byte[] data)
    {
        if (data.Length < 2) return false;
        return data[0] == 0x50 && data[1] == 0x4B;
    }

    [RelayCommand]
    private async Task DownloadFiles()
    {
        try
        {
            IsDownloading = true;
            await _processImageService.DownloadImages(ProcessedFiles);
        }
        catch(Exception e)
        {
            Debug.WriteLine($"Bug at download file {e}");
        }
        finally
        {
            IsDownloading = false;
        }

    }

    private async Task GetUserTasks()
    {

        try
        {
            IsBusy = true;
            var tasks = await _taskService.GetUserTasksAsync();
            UserTasks = new ObservableCollection<UserTasksDto>(tasks);
            Debug.WriteLine($"Fetched {UserTasks.Count} user tasks.");
            Debug.WriteLine($"Original path: {UserTasks[0].OriginalFilePath}");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error fetching user tasks: {ex.Message}");
        }
        finally
        {
            Debug.WriteLine($"User tasks fetched: {UserTasks.Count}");
            IsBusy = false;
        }
    }
}