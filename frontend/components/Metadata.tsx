import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";

type TRowType =
  | {
      key: string;
      label: React.ReactNode;
      value: React.ReactNode;
    }
  | {
      key: string;
      label: React.ReactNode;
      values: {
        value: React.ReactNode;
      }[];
    };

function Header({ row }: { row: TRowType }) {
  return (
    <Typography variant="subtitle2" color="textDisabled">
      {row.label}
    </Typography>
  );
}

function Value({ row }: { row: TRowType }) {
  const { key } = row;
  const values = "value" in row ? [{ value: row.value }] : row.values;
  return values.map(({ value }, index) => (
    <Box key={`${key}:${index}`} display="flex">
      <Typography variant="subtitle2" noWrap>
        {value}
      </Typography>
    </Box>
  ));
}

export function getFilteredRows(rows: TRowType[]): TRowType[] {
  return rows.filter((row) =>
    "value" in row ? row.value : row.values.length > 0,
  );
}

export default function Metadata({
  rows,
  headerWidth = 160,
}: {
  rows: TRowType[];
  headerWidth?: number | string;
}) {
  const filteredRows = getFilteredRows(rows);
  if (filteredRows.length === 0) {
    return null;
  }
  return (
    <div>
      <Stack spacing={1} display={{ md: "none" }}>
        {filteredRows.map((row) => (
          <div key={`${row.key}-sm`}>
            <Header row={row} />
            <Value row={row} />
          </div>
        ))}
      </Stack>
      <TableContainer sx={{ display: { xs: "none", md: "block" } }}>
        <Table size="small" sx={{ tableLayout: "fixed" }}>
          <TableBody>
            {filteredRows.map((row) => (
              <TableRow key={row.key} sx={{ verticalAlign: "baseline" }}>
                <TableCell
                  component="th"
                  sx={{
                    width: headerWidth,
                    paddingLeft: 0,
                    border: "none",
                  }}
                >
                  <Header row={row} />
                </TableCell>
                <TableCell sx={{ border: "none" }}>
                  <Value row={row} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}
