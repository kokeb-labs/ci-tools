// Compliant: the ordering is expressed with the standard library, no assembly.
#ifndef KV_RULE_10_4_1_OK_HPP
#define KV_RULE_10_4_1_OK_HPP

#include <atomic>

namespace kv::rule_10_4_1::ok {

inline void barrier() { std::atomic_signal_fence(std::memory_order_seq_cst); }

}  // namespace kv::rule_10_4_1::ok

#endif  // KV_RULE_10_4_1_OK_HPP
