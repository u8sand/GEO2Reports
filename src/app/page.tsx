'use client'
import React from 'react';
import Link from 'next/link';
import './page.css';
import trpc from "@/lib/trpc/client";
// import type {inferRouterOutputs} from "@trpc/server";
// import type {AppRouter} from '@/lib/trpc/routers/_app';

// const all_notebooks = [
//   { id: 'GSE247883', title: 'Some Study', author: 'John Doe', year: 2023, num_samples: 12 },
//   { id: 'GSE247175', title: 'Some Other Study', author: 'Jane Doe', year: 2024, num_samples: 9 },
//   { id: 'GSE247176', title: 'synthetic data', author: 'Bob Smith', year: 2023, num_samples: 9 },
//   { id: 'GSE247177', title: 'more synthetic data', author: 'Jane Doe', year: 2023, num_samples: 9 },
//   { id: 'GSE247178', title: 'really really really really really really really really really really really really really really really long title', author: 'Jane Doe', year: 2023, num_samples: 9 },
// ];

export default function Home() {

    const {data, isLoading, error} = trpc.getList.useQuery();

    const all_notebooks = data || [];

    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
    <div>
        {all_notebooks.map((notebook: any) => (
        <Link href={`/reports/${notebook.GSE}`} key={notebook.GSE}>
            <div className="notebook-card cursor-pointer hover:shadow-md transition-shadow">
            <h2 className="notebook-title truncate w-full max-w-xxl overflow-hidden whitespace-nowrap">{notebook.title}</h2>
            <div className="notebook-info">
                <span className="info-label"><b>GSE:</b> <i>{notebook.GSE}</i></span>
                <span className="info-label"><b>Year:</b> <i>{notebook.year}</i></span>
                <span className="info-label"><b>Number of Samples:</b> <i>{notebook.num_samps}</i></span>
                <span className="info-label"><b>Species:</b> <i>{notebook.species}</i></span>
            </div>
            </div>
        </Link>
        ))}
    </div>
    );
}
