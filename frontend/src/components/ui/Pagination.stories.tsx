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

export const Default: Story = {
  render: () => {
    const [page, setPage] = useState(1);
    return (
      <Pagination
        currentPage={page}
        totalPages={10}
        onPageChange={setPage}
      />
    );
  },
};

export const FirstPage: Story = {
  render: () => {
    const [page, setPage] = useState(1);
    return (
      <Pagination
        currentPage={page}
        totalPages={10}
        onPageChange={setPage}
      />
    );
  },
};

export const LastPage: Story = {
  render: () => {
    const [page, setPage] = useState(10);
    return (
      <Pagination
        currentPage={page}
        totalPages={10}
        onPageChange={setPage}
      />
    );
  },
};

export const MiddlePage: Story = {
  render: () => {
    const [page, setPage] = useState(5);
    return (
      <Pagination
        currentPage={page}
        totalPages={10}
        onPageChange={setPage}
      />
    );
  },
};

export const WithInfo: Story = {
  render: () => {
    const [page, setPage] = useState(3);
    return (
      <div className="w-full">
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
  },
};

export const ManyPages: Story = {
  render: () => {
    const [page, setPage] = useState(25);
    return (
      <Pagination
        currentPage={page}
        totalPages={50}
        onPageChange={setPage}
      />
    );
  },
};

export const FewPages: Story = {
  render: () => {
    const [page, setPage] = useState(2);
    return (
      <Pagination
        currentPage={page}
        totalPages={5}
        onPageChange={setPage}
      />
    );
  },
};

export const SinglePage: Story = {
  render: () => {
    const [page, setPage] = useState(1);
    return (
      <Pagination
        currentPage={page}
        totalPages={1}
        onPageChange={setPage}
      />
    );
  },
};

export const PatientList: Story = {
  render: () => {
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
  },
};

export const CompactView: Story = {
  render: () => {
    const [page, setPage] = useState(3);
    return (
      <div className="flex justify-center">
        <Pagination
          currentPage={page}
          totalPages={7}
          onPageChange={setPage}
          showInfo={false}
        />
      </div>
    );
  },
};

export const LargeDataset: Story = {
  render: () => {
    const [page, setPage] = useState(50);
    return (
      <div className="w-full">
        <Pagination
          currentPage={page}
          totalPages={100}
          onPageChange={setPage}
          totalItems={9987}
          pageSize={100}
          showInfo={true}
        />
      </div>
    );
  },
};

export const EmergencyRoom: Story = {
  render: () => {
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
  },
};

export const WithCustomSize: Story = {
  render: () => {
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
  },
};
