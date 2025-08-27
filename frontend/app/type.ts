enum EPageType {
  LETTER_INDEX = "correspondence.LetterIndex",
  LETTER_CORPUS = "correspondence.LetterCorpus",
  LETTER = "correspondence.Letter",
}

export type TAncestors = { id: number; title: string }[];

export type TPage = {
  id: number;
  meta: {
    type: EPageType;
    detail_url: string;
    html_url: string;
    slug: string;
    first_published_at: string;
  };
  title: string;
};

export type TPageDetailed = Omit<TPage, "meta"> & {
  meta: TPage["meta"] & {
    show_in_menus: boolean;
    seo_title: string;
    search_description: string;
  };
  ancestors: TAncestors;
};

export type TPageResults<T = TPage> = {
  meta: {
    total_count: number;
  };
  items: T[];
};
