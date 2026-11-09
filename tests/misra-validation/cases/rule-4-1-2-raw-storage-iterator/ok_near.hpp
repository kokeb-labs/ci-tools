// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_RAW_STORAGE_ITERATOR_OK_NEAR_HPP
#define KV_RULE_4_1_2_RAW_STORAGE_ITERATOR_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_raw_storage_iterator::near {

// A user type with the same name in its own namespace.
struct raw_storage_iterator {
  std::uint32_t* at{nullptr};
};
inline bool set(const raw_storage_iterator& it) { return it.at != nullptr; }

}  // namespace kv::rule_4_1_2_raw_storage_iterator::near

#endif  // KV_RULE_4_1_2_RAW_STORAGE_ITERATOR_OK_NEAR_HPP
