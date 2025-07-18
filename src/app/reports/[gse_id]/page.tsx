'use client';
import trpc from '@/lib/trpc/client';

export default async function ReportPage({ params }: { params: Promise<{ gse_id: string }> }) {
  const gse_id = (await params).gse_id;
  //const [html, setHtml] = useState('');

  // useEffect(() => {
  //   fetch(`/${gse_id}/${gse_id}.html`)
  //     .then(res => res.text())
  //     .then(data => setHtml(data))
  //     .catch(err => console.error(err));
  // }, [gse_id]); 

  const { data: html = '<span>No results</span>' } = trpc.getHTML.useQuery({ id: gse_id });
  // const fetch_html = async (id: string) => {
  //   const html = trpc.getHTML.useQuery({ id });
  //   if (html) return (html)
  //     else return ('<span>No results</span>')
  // }


  return (
    <div className="notebook-content">
      <main className="flex-grow p-4">
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: html }} 
        />
      </main>
    </div>
  );
}
