using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Threading.Tasks;
using System.Windows.Media.Animation;

namespace Converto_IT008_WPF.Views.ServiceViews
{
    public partial class MarkdownToTextView : UserControl
    {
        public MarkdownToTextView()
        {
            InitializeComponent();
        }

        private void TxtInput_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateOutput();
        }

        private void Mode_Checked(object sender, RoutedEventArgs e)
        {
            if (mdViewer == null || txtOutputPlain == null) return;
            UpdateOutput();
        }

        private void UpdateOutput()
        {
            string input = txtInput.Text;

            if (radPlainText.IsChecked == true)
            {
                mdViewer.Visibility = Visibility.Collapsed;
                txtOutputPlain.Visibility = Visibility.Visible;

                txtOutputPlain.Text = ConvertMarkdownToPlainText(input);
            }
            else
            {
                txtOutputPlain.Visibility = Visibility.Collapsed;
                mdViewer.Visibility = Visibility.Visible;

                mdViewer.Markdown = input;
            }
        }

        private void BtnClear_Click(object sender, RoutedEventArgs e)
        {
            txtInput.Clear();
        }

        private string ConvertMarkdownToPlainText(string markdown)
        {
            if (string.IsNullOrEmpty(markdown)) return string.Empty;

            string plain = Regex.Replace(markdown, @"(\*\*|__)(.*?)\1", "$2");
            plain = Regex.Replace(plain, @"(\*|_)(.*?)\1", "$2");

            plain = Regex.Replace(plain, @"^#+\s+", "", RegexOptions.Multiline);

            plain = Regex.Replace(plain, @"!\[([^\]]+)\]\([^)]+\)", "$1");

            plain = Regex.Replace(plain, @"\[([^\]]+)\]\([^)]+\)", "$1");

            plain = Regex.Replace(plain, @"^>\s+", "", RegexOptions.Multiline);

            plain = Regex.Replace(plain, @"(`{1,3})(.*?)\1", "$2", RegexOptions.Singleline);

            return plain.Trim();
        }

        private async void BtnCopy_Click(object sender, RoutedEventArgs e)
        {
            string textToCopy = "";
            if (radPlainText.IsChecked == true)
            {
                textToCopy = txtOutputPlain.Text;
            }
            else
            {
                textToCopy = txtInput.Text;
            }

            if (!string.IsNullOrEmpty(textToCopy))
            {
                Clipboard.SetText(textToCopy);

                await ShowToastNotification();
            }
        }

        private async Task ShowToastNotification()
        {
            ToastNotification.Visibility = Visibility.Visible;
            ToastNotification.Opacity = 0;

            var fadeIn = new DoubleAnimation(0, 1, TimeSpan.FromSeconds(0.2));
            ToastNotification.BeginAnimation(UIElement.OpacityProperty, fadeIn);

            await Task.Delay(2000);

            var fadeOut = new DoubleAnimation(1, 0, TimeSpan.FromSeconds(0.3));

            fadeOut.Completed += (s, e) =>
            {
                ToastNotification.Visibility = Visibility.Collapsed;
            };

            ToastNotification.BeginAnimation(UIElement.OpacityProperty, fadeOut);
        }
    }
}