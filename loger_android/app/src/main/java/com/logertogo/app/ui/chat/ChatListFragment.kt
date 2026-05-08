package com.logertogo.app.ui.chat

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.logertogo.app.databinding.FragmentChatListBinding

class ChatListFragment : Fragment() {

    private var _binding: FragmentChatListBinding? = null
    private val binding get() = _binding!!

    private val viewModel: ChatViewModel by viewModels()
    private lateinit var adapter: ConversationsAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentChatListBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        observeViewModel()

        viewModel.loadConversations()
    }

    private fun setupRecyclerView() {
        adapter = ConversationsAdapter { conversation ->
            val action = ChatListFragmentDirections.actionChatListToChatDetail(conversation.id)
            findNavController().navigate(action)
        }
        binding.recyclerConversations.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = this@ChatListFragment.adapter
        }
    }

    private fun observeViewModel() {
        viewModel.conversations.observe(viewLifecycleOwner) { state ->
            binding.progressBar.visibility = if (state.isLoading) View.VISIBLE else View.GONE
            
            if (state.data != null) {
                adapter.submitList(state.data)
                binding.tvEmpty.visibility = if (state.data.isEmpty()) View.VISIBLE else View.GONE
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
