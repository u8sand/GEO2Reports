import Image from 'next/image';

import logo from 'public/images/G2R_logo.png';
import Link from 'next/link';

export default function Header() {
  return (
    <header style={{
      backgroundColor: '#eff4f5',
      padding: '1rem',
      display: 'flex',
      alignItems: 'left',
      justifyContent: 'left',
    }}>
      <Link href="/">
        <div>
          <Image src={logo} alt="GEO2Reports Logo" layout="fixed"style={{ width: '120px', marginLeft: '1rem'}} />
        </div>
      </Link>
      <div>
        <h1 style={{ fontWeight: 'bold', fontSize: '32px', color: "#315c66" }}>GEO2Reports</h1>
        <p style={{ fontSize: '20px', color: '#666' }}>A platform for generating reports from GEO datasets.</p>
      </div>
    </header>
  );
}