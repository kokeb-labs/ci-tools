// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_TEMPORARY_BUFFER_OK_NEAR_HPP
#define KV_RULE_4_1_2_TEMPORARY_BUFFER_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_temporary_buffer::near {

// A user function with the same name, in its own namespace, backed by a fixed buffer.
struct Scratch {
  std::uint32_t* first;
  std::uint32_t count;
};
inline Scratch get_temporary_buffer(std::uint32_t* storage, std::uint32_t n) { return Scratch{storage, n}; }
inline std::uint32_t count_of(const Scratch& s) { return (s.first != nullptr) ? s.count : 0U; }

}  // namespace kv::rule_4_1_2_temporary_buffer::near

#endif  // KV_RULE_4_1_2_TEMPORARY_BUFFER_OK_NEAR_HPP
