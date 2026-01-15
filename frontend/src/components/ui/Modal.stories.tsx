import type { Meta, StoryObj } from "@storybook/react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
  ModalTrigger,
} from "./Modal";
import { Button } from "./Button";

const meta = {
  title: "Components/Modal",
  component: ModalContent,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    size: {
      control: "select",
      options: ["sm", "md", "lg", "xl"],
    },
  },
} satisfies Meta<typeof ModalContent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button>Buka Modal</Button>
      </ModalTrigger>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>Konfirmasi Aksi</ModalTitle>
          <ModalDescription>
            Apakah Anda yakin ingin melanjutkan tindakan ini?
          </ModalDescription>
        </ModalHeader>
        <div className="py-4">
          <p className="text-sm text-gray-600">
            Tindakan ini akan menyimpan perubahan yang telah Anda buat.
          </p>
        </div>
        <ModalFooter>
          <Button variant="ghost">Batal</Button>
          <Button>Ya, Lanjutkan</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  ),
};

export const Small: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button>Modal Kecil</Button>
      </ModalTrigger>
      <ModalContent size="sm">
        <ModalHeader>
          <ModalTitle>Hapus Data</ModalTitle>
        </ModalHeader>
        <div className="py-4">
          <p className="text-sm text-gray-600">
            Data yang dihapus tidak dapat dikembalikan. Lanjutkan?
          </p>
        </div>
        <ModalFooter>
          <Button variant="ghost">Batal</Button>
          <Button variant="coral">Hapus</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  ),
};

export const Large: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button>Modal Besar</Button>
      </ModalTrigger>
      <ModalContent size="xl">
        <ModalHeader>
          <ModalTitle>Rincian Pasien</ModalTitle>
          <ModalDescription>
            Informasi lengkap tentang pasien dan riwayat medis
          </ModalDescription>
        </ModalHeader>
        <div className="py-4 space-y-4">
          <div>
            <h4 className="font-medium text-gray-900">Informasi Pribadi</h4>
            <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Nama:</span>
                <p className="font-medium">Ahmad Susanto</p>
              </div>
              <div>
                <span className="text-gray-500">No. RM:</span>
                <p className="font-medium">RM-2024-1234</p>
              </div>
              <div>
                <span className="text-gray-500">Usia:</span>
                <p className="font-medium">45 tahun</p>
              </div>
              <div>
                <span className="text-gray-500">Jenis Kelamin:</span>
                <p className="font-medium">Laki-laki</p>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-900">Riwayat Medis</h4>
            <ul className="mt-2 text-sm space-y-1">
              <li>• Hipertensi (diagnosa 2020)</li>
              <li>• Diabetes Mellitus Tipe 2 (diagnosa 2021)</li>
              <li>• Alergi: Penisilin</li>
            </ul>
          </div>
        </div>
        <ModalFooter>
          <Button variant="secondary">Tutup</Button>
          <Button>Edit Data</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  ),
};

export const NoFooter: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button>Info Modal</Button>
      </ModalTrigger>
      <ModalContent size="lg">
        <ModalHeader>
          <ModalTitle>Panduan Penggunaan</ModalTitle>
        </ModalHeader>
        <div className="py-4 space-y-3 text-sm">
          <p>
            Selamat datang di SIMRS. Berikut adalah panduan singkat untuk menggunakan sistem:
          </p>
          <ol className="list-decimal list-inside space-y-2 ml-4">
            <li>Pilih menu yang diinginkan dari sidebar</li>
            <li>Cari pasien menggunakan fitur pencarian (Ctrl+K)</li>
            <li>Isi formulir dengan lengkap dan benar</li>
            <li>Klik simpan untuk menyimpan data</li>
          </ol>
          <p className="text-gray-500">
            Tekan ESC atau klik tombol X untuk menutup modal ini.
          </p>
        </div>
      </ModalContent>
    </Modal>
  ),
};

export const BPJSVerification: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button variant="primary">Verifikasi BPJS</Button>
      </ModalTrigger>
      <ModalContent size="lg">
        <ModalHeader>
          <ModalTitle>Verifikasi Keanggotaan BPJS</ModalTitle>
          <ModalDescription>
            Masukkan nomor kartu BPJS untuk memverifikasi kepesertaan
          </ModalDescription>
        </ModalHeader>
        <div className="py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nomor Kartu BPJS
            </label>
            <input
              type="text"
              placeholder="13 digit nomor BPJS"
              className="form-input"
              maxLength={13}
            />
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>Info:</strong> Verifikasi akan memeriksa status kepesertaan, faskes tujuan, dan kelas rawat.
            </p>
          </div>
        </div>
        <ModalFooter>
          <Button variant="ghost">Batal</Button>
          <Button>Verifikasi</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  ),
};

export const DischargeConfirmation: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button variant="coral">Pulangkan Pasien</Button>
      </ModalTrigger>
      <ModalContent size="lg">
        <ModalHeader>
          <ModalTitle>Konfirmasi Pulang</ModalTitle>
          <ModalDescription>
            Tinjau informasi sebelum memproses pemulangan pasien
          </ModalDescription>
        </ModalHeader>
        <div className="py-4 space-y-4">
          <div className="p-4 bg-gray-50 rounded-lg space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Pasien:</span>
              <span className="text-sm font-medium">Siti Rahayu</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">No. RM:</span>
              <span className="text-sm font-medium">RM-2024-0892</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Dirawat sejak:</span>
              <span className="text-sm font-medium">10 Jan 2026</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500"> Lama rawat:</span>
              <span className="text-sm font-medium">6 hari</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kondisi saat pulang
            </label>
            <select className="form-select">
              <option>Sembuh</option>
              <option>Membaik</option>
              <option>Stabil</option>
              <option>Tidak Membaik</option>
            </select>
          </div>
        </div>
        <ModalFooter>
          <Button variant="ghost">Batal</Button>
          <Button variant="coral">Konfirmasi Pulang</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  ),
};

export const DrugInteractionWarning: Story = {
  render: () => (
    <Modal>
      <ModalTrigger asChild>
        <Button variant="coral">Tulis Resep</Button>
      </ModalTrigger>
      <ModalContent size="lg">
        <ModalHeader>
          <ModalTitle className="text-red-600">⚠️ Interaksi Obat Terdeteksi</ModalTitle>
          <ModalDescription>
            Potensi interaksi obat yang perlu diperhatikan
          </ModalDescription>
        </ModalHeader>
        <div className="py-4 space-y-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 className="font-medium text-red-900 mb-2">Warfarin + Aspirin</h4>
            <p className="text-sm text-red-800">
              Risiko perdarahan meningkat. Pertimbangkan pemantauan INR lebih sering.
            </p>
          </div>
          <div>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="form-checkbox" />
              <span className="text-sm">Saya memahami risiko interaksi obat</span>
            </label>
          </div>
        </div>
        <ModalFooter>
          <Button variant="ghost">Batal Resep</Button>
          <Button variant="coral">Lanjutkan dengan Risiko</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  ),
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-4">
      <Modal>
        <ModalTrigger asChild>
          <Button size="sm">Small</Button>
        </ModalTrigger>
        <ModalContent size="sm">
          <ModalHeader>
            <ModalTitle>Modal Kecil</ModalTitle>
          </ModalHeader>
          <div className="py-4">
            <p className="text-sm">Modal dengan ukuran kecil (max-w-sm).</p>
          </div>
        </ModalContent>
      </Modal>

      <Modal>
        <ModalTrigger asChild>
          <Button size="sm">Medium</Button>
        </ModalTrigger>
        <ModalContent size="md">
          <ModalHeader>
            <ModalTitle>Modal Sedang</ModalTitle>
          </ModalHeader>
          <div className="py-4">
            <p className="text-sm">Modal dengan ukuran sedang (max-w-md).</p>
          </div>
        </ModalContent>
      </Modal>

      <Modal>
        <ModalTrigger asChild>
          <Button size="sm">Large</Button>
        </ModalTrigger>
        <ModalContent size="lg">
          <ModalHeader>
            <ModalTitle>Modal Besar</ModalTitle>
          </ModalHeader>
          <div className="py-4">
            <p className="text-sm">Modal dengan ukuran besar (max-w-lg).</p>
          </div>
        </ModalContent>
      </Modal>

      <Modal>
        <ModalTrigger asChild>
          <Button size="sm">Extra Large</Button>
        </ModalTrigger>
        <ModalContent size="xl">
          <ModalHeader>
            <ModalTitle>Modal Extra Besar</ModalTitle>
          </ModalHeader>
          <div className="py-4">
            <p className="text-sm">Modal dengan ukuran extra besar (max-w-xl).</p>
          </div>
        </ModalContent>
      </Modal>
    </div>
  ),
};
