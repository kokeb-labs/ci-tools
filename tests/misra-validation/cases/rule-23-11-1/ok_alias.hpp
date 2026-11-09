// Compliant near miss: the shared_ptr aliasing constructor shares ownership with an existing owner; it takes no
// ownership of the raw pointer it is given, so the guideline does not apply.
#ifndef KV_RULE_23_11_1_OK_ALIAS_HPP
#define KV_RULE_23_11_1_OK_ALIAS_HPP

#include <cstdint>
#include <memory>

namespace kv::rule_23_11_1::ok_alias {

struct Sensor {
  std::int32_t id;
};

[[nodiscard]] inline std::shared_ptr<std::int32_t> id_of(const std::shared_ptr<Sensor>& owner) {
  return std::shared_ptr<std::int32_t>(owner, &owner->id);
}

}  // namespace kv::rule_23_11_1::ok_alias

#endif  // KV_RULE_23_11_1_OK_ALIAS_HPP
