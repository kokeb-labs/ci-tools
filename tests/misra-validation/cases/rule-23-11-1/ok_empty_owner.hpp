// Compliant near miss: owners that start empty, and an owner replaced from make_unique.
#ifndef KV_RULE_23_11_1_OK_EMPTY_OWNER_HPP
#define KV_RULE_23_11_1_OK_EMPTY_OWNER_HPP

#include <cstdint>
#include <memory>

namespace kv::rule_23_11_1::ok_empty_owner {

struct Sensor {
  std::int32_t id;
};

inline void replace(std::unique_ptr<Sensor>& owner) { owner = std::make_unique<Sensor>(Sensor{3}); }

[[nodiscard]] inline std::int32_t id_or_zero(const std::unique_ptr<Sensor>& owner) {
  return (owner != nullptr) ? owner->id : 0;
}

[[nodiscard]] inline bool empty_owners() {
  const std::unique_ptr<Sensor> none{};
  const std::shared_ptr<Sensor> shared_none{nullptr};
  return (none == nullptr) && (shared_none == nullptr);
}

}  // namespace kv::rule_23_11_1::ok_empty_owner

#endif  // KV_RULE_23_11_1_OK_EMPTY_OWNER_HPP
