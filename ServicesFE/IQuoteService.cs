using Converto_IT008_WPF.Dto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE;

public interface IQuoteService
{
    public QuoteDto GetQuoteofTheDay();
}
