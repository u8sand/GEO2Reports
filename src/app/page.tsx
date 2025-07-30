'use client'
import React from 'react';
import Link from 'next/link';
import './page.css';
import trpc from "@/lib/trpc/client";

type Notebook = {
    id: string;
    title: string;
    keywords: string;
    year: number;
    num_samps: number;
    species: string;
}

export default function Home() {

    const [search, getSearch] = React.useState("");
    const [querySearch, getQuerySearch] = React.useState("")
    const [species, getSpecies] = React.useState("");
    const {data, isLoading, error} = trpc.getList.useQuery({search: querySearch, species: species});

    const handleClick = () => {
        getQuerySearch(search);
    }

    const handleEnterKey = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            handleClick();
        }
    }
    
    const all_notebooks = (data || []) as Notebook[]; //forces type conversion; Python end should ensure no null fields.

    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div>
            <div className="search-container flex justify-space-between gap-2 flex-wrap">
                <div className="join flex max-w-xl w-full">                    
                    <input
                        type="text"
                        className="search-input join-item flex border w-full max-w-xl"
                        placeholder="Search by GSE or metadata..."
                        value={search}
                        onChange={(e) => getSearch(e.target.value)}
                        onKeyDown={handleEnterKey}
                    />
                    <button onClick={handleClick} className="btn join-item text-white 
                        bg-blue-700 hover:bg-blue-800 
                        focus:ring-4 focus:ring-blue-300 font-medium 
                        rounded-lg text-sm px-5 py-2.5 me-2 mb-0 dark:bg-blue-600 
                        dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Search</button>                    
                </div>
                <select className="species-select border"
                    value={species} onChange={(e) => getSpecies(e.target.value)}>
                    <option value="">All species</option>
                    <option value="human">Human</option>
                    <option value="mouse">Mouse</option>
                </select>                
            </div>

            <div className = "notebook-list">
                {all_notebooks.map((notebook: Notebook) => (
                <Link href={`/reports/${notebook.id}`} key={notebook.id}>
                    <div className="notebook-card cursor-pointer hover:shadow-md transition-shadow">
                    <h2 className="notebook-title truncate w-full max-w-xxl overflow-hidden whitespace-nowrap">{notebook.title}</h2>
                    <h3 className="notebook-info"><b>Keywords:</b> {notebook.keywords}</h3>
                    <div className="notebook-info">
                        <span className="info-label"><b>GSE:</b> <i>{notebook.id}</i></span>
                        <span className="info-label"><b>Year:</b> <i>{notebook.year}</i></span>
                        <span className="info-label"><b>Samples:</b> <i>{notebook.num_samps}</i></span>
                        <span className="info-label"><b>Species:</b> <i>{notebook.species}</i></span>
                    </div>
                    </div>
                </Link>
                ))}
            </div>
        </div>
    );
}
