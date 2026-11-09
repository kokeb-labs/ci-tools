// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_ARRAY_DELETE_TYPE_OK_HPP
#define KV_RULE_4_1_3_ARRAY_DELETE_TYPE_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_array_delete_type::ok {

struct Item {
  std::uint32_t a{0U};
};

inline std::uint32_t first(const Item& i) { return i.a; }

}  // namespace kv::rule_4_1_3_array_delete_type::ok

#endif  // KV_RULE_4_1_3_ARRAY_DELETE_TYPE_OK_HPP
