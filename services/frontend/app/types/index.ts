export enum InputSize {
  XS = "xs",
  SM = "sm",
  MD = "md",
}

export enum Rating {
  LIKE = "Like",
  DISLIKE = "Dislike",
}

export type UserFormProps = {
  email: string;
  password: string;
};

export type InputProps = {
  type?: string;
  label?: string;
  id?: string;
  placeholder?: string;
  prefix?: React.ReactNode | null;
  suffix?: React.ReactNode | null;
  disabled?: boolean;
  error?: string;
  inputRef?: React.RefObject<HTMLInputElement> | null;
  className?: string;
  containerClassName?: string;
  size?: InputSize;
  onBlur?: () => void;
  onFocus?: () => void;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "size">;

export type NotificationProps = { status: string; content: string };
export type NotificationContextProps = {
  notifications: NotificationProps[];
  handleAddNotification: (notification: NotificationProps) => void;
};

export type LawReferenceType = {
  text: string;
  law_name: string;
  law_code: string;
  url: string;
  score: number;
};

export type MappedLawReferenceByNameType = Record<string, LawReferenceType[]>;

export class ResponseError extends Error {
  response: any;
  constructor(message: any, res: any) {
    super(message);
    this.response = res;
  }
}

export type ChatType = {
  id: string;
  customID?: string;
  question: string;
  answer: string | null;
  chat_room_id: string;
  inference_id: string;
  user_id: string;
  rating: string | null;
  feedback?: string | null,
  law_references?: LawReferenceType[] | null
  created_at: string;
  updated_at: string;
  status?: string;
  loadingState?: boolean
  loadingRef?: boolean
}

export type ChatRoomType = {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  chats: ChatType[]
}

export type InferenceModelType = {
  id: string;
  name: string;
  domain: string;
  available: boolean | null;
  llm_name: string;
  created_at: string;
  updated_at: string;
}
