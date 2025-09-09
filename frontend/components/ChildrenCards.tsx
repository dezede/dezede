import { TPageCard } from "@/app/types";
import { fetchPages } from "@/app/utils";
import PagesRowBlock from "@/blocks/PagesRowBlock";

export default async function ChildrenCards({ pageId }: { pageId: number }) {
  const childrenData = await fetchPages<TPageCard>(
    "/api/pages/",
    { child_of: pageId },
    ["search_description", "teaser_thumbnail"],
  );
  return (
    <PagesRowBlock
      block={{ id: "", value: childrenData.items, type: "pages_row" }}
    />
  );
}
