// Near misses (near): fences from the standard library and an asm-like name.
#ifndef KV_RULE_10_4_1_OK_NEAR_HPP
#define KV_RULE_10_4_1_OK_NEAR_HPP

#include <atomic>
#include <cstdint>

namespace kv::rule_10_4_1::ok_near {

inline void assemble_barrier() { std::atomic_thread_fence(std::memory_order_seq_cst); }

inline std::uint32_t asm_free(std::uint32_t v) { return v | 1U; }

}  // namespace kv::rule_10_4_1::ok_near

#endif  // KV_RULE_10_4_1_OK_NEAR_HPP
