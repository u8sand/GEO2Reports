import labLogo from 'public/images/lab_logo.png';
import mssmLogo from 'public/images/mssm_logo.png';
import Image from 'next/image';

export default function Footer() {
  return (
    <footer style={{
      backgroundColor: '#fafafa',
      padding: '2rem',
      display: 'flex', 
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      <Image src={labLogo} alt="Lab Logo" style={{ width: '160px', marginLeft: '2rem'}} />
      <p style={{ fontSize: '16px', color: '#666' }}>&copy; GEO2Reports. All rights reserved.</p>
      <Image src={mssmLogo} alt="MSSM Logo" style={{ width: '160px', marginRight: '2rem'}} />
    </footer>
  );
};