using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class QuoteServiceImpl : IQuoteService
{
    private List<QuoteDto> quotes;
    private Random random = new Random();
    
    public QuoteServiceImpl()
    {
        LoadQuote();
    }

    private void LoadQuote()
    {
        string quote = File.ReadAllText("Resources/quotes.json");
        quotes = System.Text.Json.JsonSerializer.Deserialize<List<QuoteDto>>(quote) ?? new List<QuoteDto>();
    }

    public QuoteDto GetQuoteofTheDay()
    {
        if(quotes == null || quotes.Count == 0)
        {
            LoadQuote();
        }

        int index = random.Next(quotes.Count);
        return quotes[index];
    }
}
