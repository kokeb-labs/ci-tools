// Seeded violation: a hand-written destructor and no declared copy or move members.
#include <cstdint>

namespace kv::rule_15_0_1::bad_dtor {

class Lock {  // seeded
 public:
  explicit Lock(std::uint32_t id) : id_(id) {}
  ~Lock() { id_ = 0U; }

  [[nodiscard]] std::uint32_t id() const { return id_; }

 private:
  std::uint32_t id_;
};

std::uint32_t copy_id(const Lock& l) {
  Lock c(l);
  return c.id();
}

}  // namespace kv::rule_15_0_1::bad_dtor
