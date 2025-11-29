using System.Windows.Controls;

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
            mdViewer.Markdown = txtInput.Text;
        }
    }
}