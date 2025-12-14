using Converto;
using Converto_IT008_WPF.ViewModels;
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace Converto_IT008_WPF.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow(MainWindowViewModel vm)
        {
            InitializeComponent();
            DataContext = vm;

            Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            UpdateTitleBarColor();

            if (BtnDashboard != null)
            {
                MoveIndicator(BtnDashboard, false);
            }
        }


        [DllImport("dwmapi.dll")]
        private static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);

        private const int DWMWA_USE_IMMERSIVE_DARK_MODE = 20;
        private const int DWMWA_CAPTION_COLOR = 35;
        private const int DWMWA_TEXT_COLOR = 36;

        private void UpdateTitleBarColor()
        {
            var helper = new WindowInteropHelper(this);
            IntPtr hwnd = helper.Handle;

            int useDarkMode = 1;
            DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ref useDarkMode, sizeof(int));

            int darkBackgroundColor = 0x001F1F1F;

            int whiteTextColor = 0x00FFFFFF;

            DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ref darkBackgroundColor, sizeof(int));

            DwmSetWindowAttribute(hwnd, DWMWA_TEXT_COLOR, ref whiteTextColor, sizeof(int));
        }

        private void MainWindow_Closing(object sender, CancelEventArgs e)
        {
            ExitConfirmationDialog dialog = new ExitConfirmationDialog();
            dialog.Owner = this;

            bool? result = dialog.ShowDialog();

            if (result == true)
            {
                Application.Current.Shutdown();
            }
            else
            {
                e.Cancel = true;
            }
        }

        private void SidebarButton_Click(object sender, RoutedEventArgs e)
        {
            var button = sender as RadioButton;
            MoveIndicator(button, true);
        }

        private void MoveIndicator(RadioButton button, bool animate)
        {
            if (button == null) return;

            Point relativePoint = button.TranslatePoint(new Point(0, 0), SidebarGrid);

            double targetHeight = button.ActualHeight;
            if (targetHeight == 0) targetHeight = 45;

            ActiveIndicator.Height = targetHeight;
            ActiveIndicator.Visibility = Visibility.Visible;

            double targetY = relativePoint.Y;

            if (animate)
            {
                DoubleAnimation animation = new DoubleAnimation();
                animation.To = targetY;
                animation.Duration = TimeSpan.FromMilliseconds(300);
                animation.EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut };

                IndicatorTransform.BeginAnimation(TranslateTransform.YProperty, animation);
            }
            else
            {
                IndicatorTransform.Y = targetY;
            }
        }
    }
}