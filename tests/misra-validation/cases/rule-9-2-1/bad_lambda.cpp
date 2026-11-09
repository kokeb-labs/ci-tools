// Seeded violation (lambda): a functional-notation conversion to a class type as a statement inside a lambda body.
#include <cstdint>

namespace kv::rule_9_2_1::bad_lambda {

class Lock {
 public:
  explicit Lock(std::int32_t id) : id_(id) {}
  std::int32_t id() const { return id_; }

 private:
  std::int32_t id_;
};

std::int32_t run(std::int32_t id) {
  const auto body = [id]() {
    Lock{id};  // seeded
    return id;
  };
  return body();
}

}  // namespace kv::rule_9_2_1::bad_lambda
