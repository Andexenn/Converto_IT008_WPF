using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Win32;

namespace Converto_IT008_WPF.ViewModels.ConvertServiceViewModel;

public partial class WEBPtoPNGViewModel : BaseViewModel
{
    INavigationService _navigationService;
    public WEBPtoPNGViewModel(INavigationService navigationService)
    {
        _navigationService = navigationService;
    }

    [RelayCommand]
    void GoBack()
    {
        _navigationService.Navigate<HomepageViewModel>();
    }

    [RelayCommand]
    void OpenFolder(string folderPath)
    {
        try
        {
            var dlg = new OpenFileDialog();
            dlg.Filter = "All files (*.*)|*.*";
            if (dlg.ShowDialog() == true)
            {
                var file = dlg.FileName;
            }
        }
        catch (Exception ex)
        {
            // Xử lý lỗi khi mở thư mục
            System.Windows.MessageBox.Show($"Không thể mở thư mục: {ex.Message}", "Lỗi", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
        }
    }
}
