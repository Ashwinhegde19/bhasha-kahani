import { create } from 'zustand';
import { Story, StoryDetail, StoryNode, Choice } from '@/types';

interface StoryState {
  currentStory: StoryDetail | null;
  currentNode: StoryNode | null;
  choicesMade: { nodeId: string; choiceKey: string; timestamp: string }[];
  isPlaying: boolean;
  playbackHistory: StoryNode[];
  setCurrentStory: (story: StoryDetail) => void;
  setCurrentNode: (node: StoryNode) => void;
  makeChoice: (choice: Choice) => void;
  setIsPlaying: (isPlaying: boolean) => void;
  goBack: () => void;
  reset: () => void;
}

export const useStoryStore = create<StoryState>()((set, get) => ({
  currentStory: null,
  currentNode: null,
  choicesMade: [],
  isPlaying: false,
  playbackHistory: [],
  
  setCurrentStory: (story) => {
    const startNode = story.nodes.find((n) => n.is_start);
    set({
      currentStory: story,
      currentNode: startNode || null,
      choicesMade: [],
      playbackHistory: startNode ? [startNode] : [],
    });
  },
  
  setCurrentNode: (node) => {
    const { playbackHistory } = get();
    set({
      currentNode: node,
      playbackHistory: [...playbackHistory, node],
    });
  },
  
  makeChoice: (choice) => {
    const { currentStory, currentNode, choicesMade } = get();
    if (!currentStory || !currentNode) return;
    
    const nextNode = currentStory.nodes.find((n) => n.id === choice.next_node_id);
    if (nextNode) {
      set({
        currentNode: nextNode,
        choicesMade: [
          ...choicesMade,
          {
            nodeId: currentNode.id,
            choiceKey: choice.choice_key,
            timestamp: new Date().toISOString(),
          },
        ],
        playbackHistory: [...get().playbackHistory, nextNode],
      });
    }
  },
  
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  
  goBack: () => {
    const { playbackHistory } = get();
    if (playbackHistory.length > 1) {
      const newHistory = playbackHistory.slice(0, -1);
      set({
        currentNode: newHistory[newHistory.length - 1],
        playbackHistory: newHistory,
      });
    }
  },
  
  reset: () => {
    set({
      currentStory: null,
      currentNode: null,
      choicesMade: [],
      isPlaying: false,
      playbackHistory: [],
    });
  },
}));
