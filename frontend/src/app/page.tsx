import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-5xl font-bold text-primary-700 mb-4">
            SIMRS
          </h1>
          <p className="text-xl text-neutral-600">
            Sistem Informasi Manajemen Rumah Sakit
          </p>
          <p className="text-neutral-500 mt-2">
            Modern Healthcare Management for Indonesia
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-semibold text-primary-700 mb-4">
              Selamat Datang
            </h2>
            <p className="text-neutral-600 mb-6">
              SIMRS adalah sistem informasi manajemen rumah sakit terintegrasi
              yang dirancang khusus untuk fasilitas kesehatan di Indonesia.
              Sistem ini mendukung integrasi dengan BPJS Kesehatan dan
              SATUSEHAT sesuai regulasi Kementerian Kesehatan RI.
            </p>

            <div className="grid md:grid-cols-2 gap-6 mt-8">
              <div className="border border-neutral-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-primary-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-2">
                  Keamanan Data
                </h3>
                <p className="text-sm text-neutral-600">
                  Memenuhi standar keamanan UU 27/2022 perlindungan data pribadi
                </p>
              </div>

              <div className="border border-neutral-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-2">
                  Offline-First
                </h3>
                <p className="text-sm text-neutral-600">
                  Tetap dapat digunakan tanpa koneksi internet untuk area terpencil
                </p>
              </div>

              <div className="border border-neutral-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-primary-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-2">
                  Integrasi BPJS
                </h3>
                <p className="text-sm text-neutral-600">
                  Integrasi penuh dengan VClaim, Antrean, dan SATUSEHAT FHIR
                </p>
              </div>

              <div className="border border-neutral-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-2">
                  Mudah Dikonfigurasi
                </h3>
                <p className="text-sm text-neutral-600">
                  Satu perintah untuk deploy dan konfigurasi otomatis
                </p>
              </div>
            </div>
          </div>

          {/* Status Cards */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">40</div>
              <div className="text-sm text-neutral-600">MVP Stories</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-accent-600 mb-2">15</div>
              <div className="text-sm text-neutral-600">Epics</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">419</div>
              <div className="text-sm text-neutral-600">Story Points</div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <a
              href="/docs"
              className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              API Documentation
            </a>
            <a
              href="/redoc"
              className="inline-flex items-center px-6 py-3 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              ReDoc
            </a>
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-16 text-sm text-neutral-500">
          <p>SIMRS v1.0.0 | Sistem Informasi Manajemen Rumah Sakit</p>
          <p className="mt-1">Compliant with Permenkes 24/2022 & Permenkes 82/2013</p>
        </footer>
      </div>
    </div>
  );
}
