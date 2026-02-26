import type { Meta, StoryObj } from "@storybook/react";
import { Pagination } from "./Pagination";
import { useState } from "react";

const meta = {
  title: "Components/Pagination",
  component: Pagination,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Pagination>;

export default meta;
type Story = StoryObj<typeof meta>;

// Wrapper component to handle state
const PaginationWrapper = ({ initialPage = 1, totalPages = 10, totalItems, pageSize, showInfo }: {
  initialPage?: number;
  totalPages: number;
  totalItems?: number;
  pageSize?: number;
  showInfo?: boolean;
}) => {
  const [page, setPage] = useState(initialPage);
  return (
    <Pagination
      currentPage={page}
      totalPages={totalPages}
      onPageChange={setPage}
      totalItems={totalItems}
      pageSize={pageSize}
      showInfo={showInfo}
    />
  );
};

export const Default: Story = {
  render: () => <PaginationWrapper totalPages={10} />,
};

export const FirstPage: Story = {
  render: () => <PaginationWrapper initialPage={1} totalPages={10} />,
};

export const LastPage: Story = {
  render: () => <PaginationWrapper initialPage={10} totalPages={10} />,
};

export const MiddlePage: Story = {
  render: () => <PaginationWrapper initialPage={5} totalPages={10} />,
};

export const WithInfo: Story = {
  render: () => (
    <div className="w-full">
      <PaginationWrapper initialPage={3} totalPages={10} totalItems={95} pageSize={10} showInfo={true} />
    </div>
  ),
};

export const ManyPages: Story = {
  render: () => <PaginationWrapper initialPage={25} totalPages={50} />,
};

export const FewPages: Story = {
  render: () => <PaginationWrapper initialPage={2} totalPages={5} />,
};

export const SinglePage: Story = {
  render: () => <PaginationWrapper initialPage={1} totalPages={1} />,
};

const PatientListWrapper = () => {
  const [page, setPage] = useState(1);
  return (
    <div className="w-full">
      <div className="mb-4 p-4 bg-white border rounded">
        <p className="text-sm text-gray-600">Daftar Pasien Rawat Inap</p>
        <p className="text-xs text-gray-500 mt-1">Halaman {page} dari 10</p>
      </div>
      <Pagination
        currentPage={page}
        totalPages={10}
        onPageChange={setPage}
        totalItems={95}
        pageSize={10}
        showInfo={true}
      />
    </div>
  );
};

export const PatientList: Story = {
  render: () => <PatientListWrapper />,
};

export const CompactView: Story = {
  render: () => (
    <div className="flex justify-center">
      <PaginationWrapper initialPage={3} totalPages={7} showInfo={false} />
    </div>
  ),
};

export const LargeDataset: Story = {
  render: () => (
    <div className="w-full">
      <PaginationWrapper initialPage={50} totalPages={100} totalItems={9987} pageSize={100} showInfo={true} />
    </div>
  ),
};

const EmergencyRoomWrapper = () => {
  const [page, setPage] = useState(1);
  return (
    <div className="w-full">
      <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
        <p className="font-medium text-red-900">Antrian IGD</p>
        <p className="text-sm text-red-700 mt-1">
          {page === 1 ? "Pasien Gawat Darurat" : `Antrian prioritas - Halaman ${page}`}
        </p>
      </div>
      <Pagination
        currentPage={page}
        totalPages={15}
        onPageChange={setPage}
        totalItems={142}
        pageSize={10}
        showInfo={true}
      />
    </div>
  );
};

export const EmergencyRoom: Story = {
  render: () => <EmergencyRoomWrapper />,
};

const WithCustomSizeWrapper = () => {
  const [page, setPage] = useState(1);
  return (
    <div className="w-full">
      <Pagination
        currentPage={page}
        totalPages={20}
        onPageChange={setPage}
        totalItems={198}
        pageSize={10}
        showInfo={true}
      />
      <p className="text-xs text-gray-500 mt-2 text-center">
        10 pasien per halaman
      </p>
    </div>
  );
};

export const WithCustomSize: Story = {
  render: () => <WithCustomSizeWrapper />,
};