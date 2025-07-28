'use client';
import trpc from '@/lib/trpc/client';
import React from 'react';
import './style.css'

export default function ReportPage(props: { params: Promise<{ gse_id: string }> }) {
  const params = React.use(props.params)
  
  const { data, isLoading, error } = trpc.getHTML.useQuery({ id: params.gse_id });

  const html = data || '';

  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    return <div>Error: {error.message}</div>;
  }
  
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